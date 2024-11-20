from typing import List, Dict, Any, Type, Optional, TypeVar, Generic, Set, Callable
from dataclasses import dataclass
from collections import defaultdict
from datetime import datetime
from sqlmodel import SQLModel, select, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar
import asyncio

from ...utils.pydantic_models.record import (
    RecordBaseModel,
    PersonName,
    VoterRegistration,
    VEPMatch,
    InputData,
    AddressLink,
    PhoneLink,
    ElectionVote,
)
from ...utils.pydantic_models.cleanup_model import PreValidationCleanUp


T = TypeVar('T', bound=SQLModel)


class EntityBuffer(Generic[T]):
    """Buffers entities for bulk loading to reduce database queries."""
    def __init__(self, model_type: Type[T], batch_size: int = 1000):
        self.model_type = model_type
        self.entities: Dict[str, T] = {}
        self.batch_size = batch_size
        self.processed_keys: Set[str] = set()

    def add(self, key: str, entity: T) -> None:
        """Add entity to buffer if not already processed."""
        if key not in self.processed_keys:
            self.entities[key] = entity

    def should_flush(self) -> bool:
        """Check if buffer should be flushed."""
        return len(self.entities) >= self.batch_size

    def get_and_clear(self) -> Dict[str, T]:
        """Get entities and clear buffer."""
        entities = self.entities.copy()
        self.processed_keys.update(self.entities.keys())
        self.entities.clear()
        return entities


class RecordLoader:
    """Handles efficient loading of records and related entities using SQLModel."""

    def __init__(self, session: AsyncSession, buffer_size: int = 1000):
        self.session = session
        self.buffers: Dict[Type[SQLModel], EntityBuffer] = {}
        self.buffer_size = buffer_size
        self.loaded_entities: Dict[Type[SQLModel], Dict[str, SQLModel]] = defaultdict(dict)

    def get_buffer(self, model_type: Type[SQLModel]) -> EntityBuffer:
        """Get or create buffer for model type."""
        if model_type not in self.buffers:
            self.buffers[model_type] = EntityBuffer(model_type, self.buffer_size)
        return self.buffers[model_type]

    async def _load_entities_async(
            self,
            model_type: Type[SQLModel],
            keys: List[str],
            id_field: str
    ) -> Dict[str, SQLModel]:
        """Load entities by their keys asynchronously."""
        if not keys:
            return {}

        stmt = select(model_type).where(getattr(model_type, id_field).in_(keys))
        result = await self.session.execute(stmt)
        entities = result.scalars().all()
        return {getattr(entity, id_field): entity for entity in entities}

    def _load_entities_sync(
            self,
            model_type: Type[SQLModel],
            keys: List[str],
            id_field: str
    ) -> Dict[str, SQLModel]:
        """Load entities by their keys synchronously."""
        if not keys:
            return {}

        stmt = select(model_type).where(getattr(model_type, id_field).in_(keys))
        result = self.session.exec(stmt)
        return {getattr(entity, id_field): entity for entity in result.all()}

    async def process_record_async(self, record_data: "PreValidationCleanUp") -> None:
        """Process a single record asynchronously."""
        # Buffer core entities
        self.get_buffer(PersonName).add(record_data.name.id, record_data.name)
        self.get_buffer(VoterRegistration).add(record_data.voter_registration.vuid, record_data.voter_registration)
        self.get_buffer(VEPMatch).add(record_data.vep_keys.id, record_data.vep_keys)
        self.get_buffer(InputData).add(record_data.input_data.id, record_data.input_data)

        # Process each buffer if needed
        for model_type, buffer in self.buffers.items():
            if buffer.should_flush():
                entities = buffer.get_and_clear()
                id_field = self._get_id_field(model_type)
                existing = await self._load_entities_async(model_type, list(entities.keys()), id_field)

                # Merge new entities with existing ones
                for key, entity in entities.items():
                    if key not in existing:
                        self.session.add(entity)
                    self.loaded_entities[model_type][key] = existing.get(key, entity)

    def process_record_sync(self, record_data: "PreValidationCleanUp") -> None:
        """Process a single record synchronously."""
        # Buffer core entities
        self.get_buffer(PersonName).add(record_data.name.id, record_data.name)
        self.get_buffer(VoterRegistration).add(record_data.voter_registration.vuid, record_data.voter_registration)
        self.get_buffer(VEPMatch).add(record_data.vep_keys.id, record_data.vep_keys)
        self.get_buffer(InputData).add(record_data.input_data.id, record_data.input_data)

        # Process each buffer if needed
        for model_type, buffer in self.buffers.items():
            if buffer.should_flush():
                entities = buffer.get_and_clear()
                id_field = self._get_id_field(model_type)
                existing = self._load_entities_sync(model_type, list(entities.keys()), id_field)

                # Merge new entities with existing ones
                for key, entity in entities.items():
                    if key not in existing:
                        self.session.add(entity)
                    self.loaded_entities[model_type][key] = existing.get(key, entity)

    def _get_id_field(self, model_type: Type[SQLModel]) -> str:
        """Get the appropriate ID field for the model type."""
        if model_type == VoterRegistration:
            return 'vuid'
        return 'id'

    async def create_record_async(self, record_data: "PreValidationCleanUp", _validator_model: Type["RecordBaseModel"]) -> "RecordBaseModel":
        """Create a record with all its relationships asynchronously."""
        await self.process_record_async(record_data)

        # Create the record
        record = _validator_model(
            name_id=record_data.name.id,
            voter_registration_id=record_data.voter_registration.vuid,
            vep_keys_id=record_data.vep_keys.id,
            input_data_id=record_data.input_data.id,
        )

        self.session.add(record)
        await self.session.flush()

        # Handle relationships
        await self._handle_relationships_async(record, record_data)

        return record

    def create_record_sync(self, record_data: "PreValidationCleanUp", _validator_model: Type["RecordBaseModel"]) -> "RecordBaseModel":
        """Create a record with all its relationships synchronously."""
        self.process_record_sync(record_data)

        # Create the record
        record = _validator_model(
            name_id=record_data.name.id,
            voter_registration_id=record_data.voter_registration.vuid,
            vep_keys_id=record_data.vep_keys.id,
            input_data_id=record_data.input_data.id,
        )

        self.session.add(record)
        self.session.flush()

        # Handle relationships
        self._handle_relationships_sync(record, record_data)

        return record

    async def _handle_relationships_async(
            self,
            record: "RecordBaseModel",
            record_data: "PreValidationCleanUp"
    ) -> None:
        """Handle loading and linking of relationships asynchronously."""
        # Handle addresses
        if record_data.address_list:
            for address in record_data.address_list:
                link = AddressLink(
                    address_id=address.id,
                    record_id=record.id,
                )
                self.session.add(link)

        # Handle phone numbers
        if record_data.phone:
            for phone in record_data.phone:
                link = PhoneLink(
                    phone_id=phone.id,
                    record_id=record.id
                )
                self.session.add(link)

        # Handle elections
        if record_data.elections:
            for election in record_data.elections:
                vote_record = ElectionVote(
                    election_id=election.id,
                    record_id=record.id,
                    vote_method=election.vote_method,
                    vote_date=election.vote_date
                )
                self.session.add(vote_record)

        # Handle data sources
        if record_data.data_source:
            for source in record_data.data_source:
                link = DataSourceLink(
                    data_source_id=source.id,
                    record_id=record.id
                )
                self.session.add(link)

    def _handle_relationships_sync(
            self,
            record: RecordBaseModel,
            record_data: PreValidationCleanUp
    ) -> None:
        """Handle loading and linking of relationships synchronously."""
        # Implementation mirrors the async version but uses sync session operations
        # Handle addresses
        if record_data.address_list:
            for address in record_data.address_list:
                link = AddressLink(
                    address_id=address.id,
                    record_id=record.id,
                )
                self.session.add(link)

        # Handle phone numbers
        if record_data.phone:
            for phone in record_data.phone:
                link = PhoneLink(
                    phone_id=phone.id,
                    record_id=record.id
                )
                self.session.add(link)

        # Handle elections
        if record_data.elections:
            for election in record_data.elections:
                vote_record = ElectionVote(
                    election_id=election.id,
                    record_id=record.id,
                    vote_method=election.vote_method,
                    vote_date=election.vote_date
                )
                self.session.add(vote_record)

        # Handle data sources
        if record_data.data_source:
            for source in record_data.data_source:
                link = DataSourceLink(
                    data_source_id=source.id,
                    record_id=record.id
                )
                self.session.add(link)


# Usage example
async def bulk_load_records_async(
        records: List["PreValidationCleanUp"],
        model: Type["RecordBaseModel"],
        session: AsyncSession
) -> List[RecordBaseModel]:
    """Bulk load records asynchronously."""
    loader = RecordLoader(session)
    result = []

    for record_data in records:
        result.append(await loader.create_record_async(record_data=record_data, _validator_model=model))

    await session.commit()
    return result


def bulk_load_records_sync(
        records: List["PreValidationCleanUp"],
        session: Session
) -> List["RecordBaseModel"]:
    """Bulk load records synchronously."""
    loader = RecordLoader(session)
    result = []

    for record_data in records:
        result.append(loader.create_record_sync(record_data))

    session.commit()
    return result