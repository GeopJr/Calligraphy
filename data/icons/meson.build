scalable_dir = join_paths('hicolor', 'scalable', 'apps')
icon_name_template = '@0@.svg'
if devel
  icon_name_template = '@0@.Devel.svg'
endif

install_data(
  join_paths(scalable_dir, (icon_name_template).format(meson.project_name())),
  install_dir: join_paths(get_option('datadir'), 'icons', scalable_dir),
  rename: meson.project_name() + '.svg',
)

symbolic_dir = join_paths('hicolor', 'symbolic', 'apps')
install_data(
  join_paths(symbolic_dir, ('@0@-symbolic.svg').format(meson.project_name())),
  install_dir: join_paths(get_option('datadir'), 'icons', symbolic_dir)
)
