from dataclasses import dataclass, field
from app.conf.config import CampaignFinanceConfig
from app.loaders.tec_loader import TECCategory
from datetime import datetime
from typing import Dict


# TODO: Change model args to _args
# TODO: Build post_init method to create validator after changing model args

@dataclass
class CreatePydanticModel:
    category: TECCategory.category
    record_category: str = CampaignFinanceConfig.RECORD_CATEGORY_TUPLE
    _record_types: Dict[str, str] = field(default_factory=dict)

    def create_record_types(self) -> Dict[str, str]:
        self._record_types = {
            key: value for key, value in [
                var for _record in next(self.category.records) for var in _record
            ]
        }
        self._record_types[CampaignFinanceConfig.RECORD_TYPE_COLUMN] = self.record_category
        return self._record_types

    def create_validator(self, validator_name: str) -> None:
        """
        Create Validator
        :return:
        """
        print(f"class {validator_name}(BaseModel):")
        for key, value in self._record_types.items():
            print(f"\t{key}: Optional[{type(value).__name__}]")

        print(f"""\tclass Config:
            \torm_mode = True
            \tallow_population_by_field_name = True
            \tvalidate_assignment = True
            \tvalidate_all = True
            \textra = 'forbid'""")

    def create_sql_model(self, model_name: str, table_name: str, schema: str = CampaignFinanceConfig.STATE) -> None:
        if table_name or schema is None:
            raise ValueError(f"""
                Table name and schema are required to create a SQL model:
                table_name: {table_name}
                schema: {schema}""")

        print(f"""class {model_name}(Base):""")
        print(f"\t__tablename__ = '{table_name}'")
        print(f"\t__table_args__ = {{'schema': '{schema.lower()}'}}")
        for _name, _type in self._record_types.items():
            if _type == str:
                _type_details = "Column(String, nullable=True)"
            elif _type == int:
                _type_details = "Column(Integer, nullable=True)"
            elif _type == float:
                _type_details = "Column(Float, nullable=True)"
            elif _type == datetime:
                _type_details = "Column(DateTime, nullable=True)"
            else:
                _type_details = "Column(String, nullable=True)"
            print(f"\t{_name} = {_type_details}")
