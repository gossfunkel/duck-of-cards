from setuptools import setup

setup(
	name = "That's my horse, duck!",
	options = {
		'build_apps': {
			# build the exe as a gui_app
			'gui_apps': {
				'thatsmyhorse': 'duckTest.py',
			},
			'icons': {
				'thatsmyhorse': ["icon-256.png"],
			},

			# output logging
			'log_filename': '$USER_APPDATA/thatsmyhorse/output.log',
			'log_appent': False,

			# specify included files
			'include_patterns': [
				'assets/roundDuck.gltf'
				'assets/heart.png'
			],

			# extensions for automatic .bam conversion
			'bam_model_extensions': ['.gltf'],

			# opengl renderer
			'plugins': [
				'pandagl',
			],
		}
	}
)