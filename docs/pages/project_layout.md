
    campaignfinance/ 

        app/
            conf/
                * config.py
                * logger.py
            funcs/
                * category_funcs.py
                * general_funcs.py
                * record_generator.py
                * validator_funcs.py
            getters/
                * tec_contribution_getter.py
                * tec_expense_getter.py
                * [DEPRECIATED] tec_universal_getter.py
            loaders/
                * [IN PROGRESS] async_tec_expenses.py
                * tec_loader.py
                * toml_loader.py
            models/
                * tec_contribution_model.py
                * tec_expense_model.py
                * tec_filer_model.py
                * [DEPRECIATED] tec_universal_model.py
            pandas_schemas/
                * tec_contribution_schema.py
                * tec_expense_schema.py
            search_tools/
                * tec_search.py
            utils/
                field_library/
                        * texas.toml
                * file_field_assigner.py
                * pydantic_builder.py
            validators/
                * tec_contribution_validator.py
                * tec_expense_validator.py
                * tec_filers_validator.py
                * [DEPRECIATED] tec_universal_validator.py
        tmp/
            
