from state_voterfiles.utils.toml_reader import TomlReader, Path

texas = TomlReader(Path(__file__).parent /'state_voterfiles' / 'field_references' / 'texas-fields.toml')
