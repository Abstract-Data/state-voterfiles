from state_voterfiles.utils.toml_reader import TomlReader, Path

texas = TomlReader(Path(__file__).parent /'state_voterfiles' / 'state_fields' / 'texas-fields.toml')
