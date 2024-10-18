from typing import Optional, Type
from pydantic.dataclasses import dataclass as pydantic_dataclass, Field as PydanticField
from sqlmodel import MetaData, SQLModel, Session, text, select
from sqlalchemy import Engine
from sqlalchemy.orm import joinedload

from state_voterfiles.utils.db_models.record import RecordBaseModel
from state_voterfiles.utils.db_models.fields.district import District
# from state_voterfiles.utils.db_models.fields.elections import ElectionLinkToRecord, ElectionLink, ElectionTypeDetails, VotedInElection
from state_voterfiles.utils.db_models.fields.address import Address, AddressLink
from state_voterfiles.utils.db_models.fields.voter_registration import VoterRegistration
from state_voterfiles.utils.db_models.fields.phone_number import PhoneLink, ValidatedPhoneNumber


@pydantic_dataclass(config={"arbitrary_types_allowed": True})
class TableManager:
    record_type: Optional[str] = None
    record_metadata: MetaData = MetaData()

    def _set_metadata(self):
        for table_name, table in SQLModel.metadata.tables.items():
            old_name = table.name
            new_name = f"{self.record_type}_{old_name}"
            table.name = new_name
            table.metadata = self.record_metadata

    def drop_db_enums(self, engine: Engine):
        query = text("""
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (
                SELECT n.nspname AS enum_schema, t.typname AS enum_name
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                GROUP BY enum_schema, enum_name)
            LOOP
                EXECUTE 'DROP TYPE ' || quote_ident(r.enum_schema) || '.' || quote_ident(r.enum_name) || ' CASCADE';
            END LOOP;
        END $$;
        """)
        with Session(engine) as session:
            session.execute(query)
            session.commit()
        return self

    @staticmethod
    def create_flat_record_view(engine: Engine):
        metadata = RecordBaseModel.metadata

        # Fetch all election type detail IDs
        with Session(engine) as session:
            election_type_ids = session.execute(
                text(f"SELECT id FROM {metadata.tables['electiontypedetails'].name}")
            ).fetchall()

            # Fetch all district types and names
            district_info = session.execute(
                text(f"SELECT type, name FROM {metadata.tables['district'].name}")
            ).fetchall()

            phone_types = session.execute(
                text(f"SELECT DISTINCT phone_type FROM {metadata.tables['validatedphonenumber'].name}")
            ).fetchall()

        election_columns = ",\n".join(
            [
                f"(SELECT STRING_AGG(CASE WHEN v.party IS NOT NULL THEN v.party::text ELSE v.vote_method::text END, ', ') "
                f"FROM {metadata.tables['votedinelection'].name} v "
                f"JOIN {metadata.tables['electionlink'].name} el ON v.id = el.vote_details_id "
                f"JOIN {metadata.tables['electionlinktorecord'].name} elr ON el.election_id = elr.election_link_id "
                f"WHERE elr.record_id = r.id AND el.election_id = '{election_id[0]}') AS election_{election_id[0].replace('-', '_')}"
                for election_id in election_type_ids
            ]
        )

        # Generate dynamic columns for each district type and name
        district_columns = ",\n".join(
            [
                f"(SELECT d.number FROM {metadata.tables['districtsetlink'].name} dsl "
                f"JOIN {metadata.tables['district'].name} d ON dsl.district_id = d.id "
                f"JOIN {metadata.tables['districtset'].name} ds ON dsl.district_set_id = ds.id "
                f"WHERE ds.id = r.district_set_id AND d.type = '{district.type}' AND d.name = '{district.name}') AS district_{district.type.replace(' ', '_').replace('-', '_')}_{district.name.replace(' ', '_').replace('-', '_')}"
                for district in district_info
            ]
        )

        # Generate dynamic columns for each phone type
        phone_columns = ",\n".join(
            [
                f"(SELECT p.phone FROM phone_link pl "
                f"JOIN {metadata.tables['validatedphonenumber']} p ON pl.phone_id = p.id "
                f"WHERE pl.record_id = r.id AND p.phone_type = '{phone_type[0]}') AS {phone_type[0].replace(' ', '_').replace('-', '_')}_phone"
                for phone_type in phone_types
            ]
        )

        drop_statement = text(f"DROP VIEW IF EXISTS flat_record_view;")

        # Construct the SELECT statement dynamically
        select_columns = [
            "r.id AS record_id",
            "vr.county AS registration_county",
            "vr.edr as registration_date",
            "pn.first AS first_name",
            "pn.middle AS middle_name",
            "pn.last AS last_name",
            "vr.vuid AS voter_id",
            "pn.dob AS dob",
            f"(SELECT STRING_AGG(a.standardized, ', ') FROM {metadata.tables['address'].name} a JOIN {metadata.tables['address_link'].name} al ON a.id = al.address_id WHERE al.record_id = r.id) AS address_std",
            f"(SELECT STRING_AGG(a.city, ', ') FROM {metadata.tables['address'].name} a JOIN {metadata.tables['address_link'].name} al ON a.id = al.address_id WHERE al.record_id = r.id) AS address_city",
            f"(SELECT STRING_AGG(a.state, ', ') FROM {metadata.tables['address'].name} a JOIN {metadata.tables['address_link'].name} al ON a.id = al.address_id WHERE al.record_id = r.id) AS address_state",
            f"(SELECT STRING_AGG(a.zip5, ', ') FROM {metadata.tables['address'].name} a JOIN {metadata.tables['address_link'].name} al ON a.id = al.address_id WHERE al.record_id = r.id) AS address_zip"
        ]

        if phone_columns:
            select_columns.append(phone_columns)
        if district_columns:
            select_columns.append(district_columns)
        if election_columns:
            select_columns.append(election_columns)

        view_sql = f"""
        CREATE OR REPLACE VIEW flat_record_view AS
        SELECT
            {',\n'.join(select_columns)}
        FROM
            {metadata.tables['recordbasemodel'].name} r
        LEFT JOIN
            {metadata.tables['person_name'].name} pn ON r.name_id = pn.id
        LEFT JOIN
            {metadata.tables['voter_registration'].name} vr ON r.voter_registration_id = vr.id
        GROUP BY
            r.id, vr.county, pn.first, pn.middle, pn.last, vr.edr, vr.vuid, pn.dob;
        """
        # view_sql = f"""
        # CREATE VIEW flat_record_view AS
        # SELECT
        #     r.id AS record_id,
        #     pn.first AS first_name,
        #     pn.last AS last_name,
        #     vr.vuid AS voter_id,
        #     pn.dob AS dob,
        #     a.standardized AS address_std,
        #     a.city AS address_city,
        #     a.state AS address_state,
        #     a.zip5 AS address_zip,
        #     d.county AS district_county,
        #     p.phone AS phone_number,
        #     e.year AS election_year,
        #     e.election_type AS election_type,
        #     v.vote_method AS vote_method,
        #     v.party AS vote_party
        # FROM
        #     {metadata.tables['recordbasemodel'].name} r
        # LEFT JOIN
        #     {metadata.tables['person_name'].name} pn ON r.name_id = pn.id
        # LEFT JOIN
        #     {metadata.tables['voter_registration'].name} vr ON r.voter_registration_id = vr.id
        # LEFT JOIN
        #     {metadata.tables['address_link'].name} al ON r.id = al.record_id
        # LEFT JOIN
        #     {metadata.tables['address'].name} a ON al.address_id = a.id
        # LEFT JOIN
        #     {metadata.tables['districtset'].name} ds ON r.district_set_id = ds.id
        # LEFT JOIN
        #     {metadata.tables['district'].name} d ON ds.id = r.district_set_id
        # LEFT JOIN
        #     {metadata.tables['phone_link'].name} pl ON r.id = pl.record_id
        # LEFT JOIN
        #     {metadata.tables['validatedphonenumber'].name} p ON pl.phone_id = p.id
        # LEFT JOIN
        #     {metadata.tables['electionlinktorecord'].name} elr ON r.id = elr.record_id
        # LEFT JOIN
        #     {metadata.tables['electionlink'].name} el ON elr.election_link_id = el.election_id
        # LEFT JOIN
        #     {metadata.tables['electiontypedetails'].name} e ON el.election_id = e.id
        # LEFT JOIN
        #     {metadata.tables['votedinelection'].name} v ON el.vote_details_id = v.id;
        # """
        with Session(engine) as session:
            session.execute(drop_statement)
            session.commit()
            session.execute(text(view_sql))
            session.commit()

    @staticmethod
    def get_all_records(engine: Engine, model: Type[SQLModel] = RecordBaseModel):
        statement = select(
            RecordBaseModel
        ).options(
            joinedload(RecordBaseModel.name),
            joinedload(RecordBaseModel.voter_registration),
            joinedload(RecordBaseModel.address_list),
            joinedload(RecordBaseModel.district_set)
            .joinedload(DistrictSet.districts),
            joinedload(RecordBaseModel.phone_numbers),
            joinedload(RecordBaseModel.election_link_records).joinedload(
                ElectionLinkToRecord.election_link).joinedload(ElectionLink.election),
            joinedload(RecordBaseModel.election_link_records).joinedload(
                ElectionLinkToRecord.election_link).joinedload(ElectionLink.vote_details),
            joinedload(RecordBaseModel.vep_keys),
            joinedload(RecordBaseModel.data_source),
        )
        with Session(engine) as session:
            results = session.exec(statement).unique().all()
        return results
