/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

const defaultTheme = require('tailwindcss/defaultTheme');
const colors = require('tailwindcss/colors');

module.exports = {
	content: [
		/**
		 * HTML. Paths to Django template files that will contain Tailwind CSS classes.
		 */

		/*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
		'../templates/**/*.html',

		/*
		 * Main templates directory of the project (BASE_DIR/templates).
		 * Adjust the following line to match your project structure.
		 */
		'../../templates/**/*.html',

		/*
		 * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
		 * Adjust the following line to match your project structure.
		 */
		'../../**/templates/**/*.html'

		/**
		 * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
		 * patterns match your project structure.
		 */
		/* JS 1: Ignore any JavaScript in node_modules folder. */
		// '!../../**/node_modules',
		/* JS 2: Process all JavaScript files in the project. */
		// '../../**/*.js',

		/**
		 * Python: If you use Tailwind CSS classes in Python, uncomment the following line
		 * and make sure the pattern below matches your project structure.
		 */
		// '../../**/*.py'
	],
	theme: {
		extend: {
			fontFamily: {
				sans: ['Poppins', ...defaultTheme.fontFamily.sans]
			},
			colors: {
				teal: colors.teal,
				cyan: colors.cyan,
				primary: 'hsl(191, 26%, 12%)',
				'primary-darken': 'hsl(191, 26%, 8%)',
				'primary-lighten': 'hsl(191, 26%, 24%)',
				'primary-semi-light': 'hsl(191, 26%, 18%)',
				accent: 'hsl(29, 94%, 50%)',
				'accent-darken': 'hsl(29, 94%, 40%)',
				'accent-lighten': 'hsl(29, 94%, 60%)',
				contrast: 'hsl(70, 19%, 87%)',
				'contrast-light': 'hsl(70, 19%, 95%)',
				'contrast-dark': 'hsl(70, 19%, 80%)',
			},
			transitionDuration: {
				0: '0ms',
				2000: '2000ms'
			},
			flex: {
				'2': '2 2 0%',
				'3': '3 3 0%'
			},
			fontSize: {
				'xxs': '.6rem',
			}
		}
	},
	plugins: [
		/**
		 * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
		 * for forms. If you don't like it or have own styling for forms,
		 * comment the line below to disable '@tailwindcss/forms'.
		 */
		require('@tailwindcss/forms'),
		require('@tailwindcss/typography'),
		require('@tailwindcss/line-clamp'),
		require('@tailwindcss/aspect-ratio')
	]
};
