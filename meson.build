project('dev.geopjr.Calligraphy',
          version: '1.0.1',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

devel = get_option('devel')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'calligraphy')

config = configuration_data()
config.set('APP_ID', meson.project_name())
config.set('PYTHON', python.find_installation('python3').full_path())
config.set('VERSION', meson.project_version())
config.set('DEVEL', devel ? 'True' : 'False')
config.set('LOCALEDIR', join_paths(get_option('prefix'), get_option('localedir')))
config.set('PKGDATADIR', pkgdatadir)

if devel
  git = find_program('git')
  if git.found()
    branch = run_command('git', 'branch', '--show-current', check: true).stdout().strip()
    revision = run_command('git', 'rev-parse', '--short', 'HEAD', check: true).stdout().strip()
    version = '@0@-@1@'.format(branch, revision)
    config.set('VERSION', version)
  endif
endif

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
