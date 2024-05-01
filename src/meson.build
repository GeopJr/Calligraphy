pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'calligraphy')
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'gtk/help-overlay.blp',
    'gtk/window.blp',
    'gtk/font-view-page.blp',
    'gtk/font-preview-card.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('calligraphy',
  'calligraphy.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: [blueprints, appstream_file],
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'calligraphy.in',
  output: 'calligraphy',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

calligraphy_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'fonts_list.py',
  'get_text_view_text.py',
  'font_view_page.py',
  'font_preview.py',
  'font_preview_card.py',
  'update_button_sensitivity.py',
]

install_data(calligraphy_sources, install_dir: moduledir)
