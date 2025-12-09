/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                space: {
                    900: '#090a0f', // Deepest Void
                    800: '#0b1021', // Dark Navy
                    700: '#1b2735', // Lighter Space
                },
                neon: {
                    blue: '#00f2ff', // Cyan Neon
                    red: '#ff3366',  // Neon Red
                },
                starlight: '#a0c4ff', // Text Blue
            },
            fontFamily: {
                mono: ['"Courier New"', 'monospace'],
                tech: ['"Rajdhani"', 'sans-serif'], // We might need to import this font
            },
            backgroundImage: {
                'deep-space': 'radial-gradient(circle at center, #1b2735 0%, #090a0f 100%)',
            },
            boxShadow: {
                'neon-blue': '0 0 10px rgba(0, 242, 255, 0.5)',
                'neon-red': '0 0 10px rgba(255, 51, 102, 0.5)',
            }
        },
    },
    plugins: [],
}
