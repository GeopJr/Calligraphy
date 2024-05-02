configure_file(
  input: 'calligraphy.in',
  output: 'calligraphy',
  configuration: config,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

sources = [
  configure_file(
    input: 'env.py.in',
    output: 'env.py',
    configuration: config
  ),
  '__init__.py',
  'main.py',
]

subdir('Utils')
subdir('Views')
subdir('Widgets')

install_data(sources, install_dir: moduledir)
