/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "primary": "#ff7a2f", // Core accent
                "secondary": "#d6d4d3",
                "tertiary": "#fbb423",
                "error": "#d53d18",
                "background": "#121212", // Charcoal
                "surface": "#1e1e1e", // Elevated
                "surface-variant": "#262626", // Tertiary elev
                "surface-container": "#2c2c2c",
                "surface-container-low": "#242424", // Defined for consistency
                "surface-container-high": "#333333",
                "surface-container-highest": "#3a3a3a",
                "on-surface": "#fcfaf8", // Off-white
                "on-surface-variant": "#b0b0b0", // High contrast gray
                "outline": "#444444",
                "outline-variant": "#333333"
            },
        },
        fontFamily: {
            "headline": ["Inter", "sans-serif"],
            "body": ["Inter", "sans-serif"],
            "label": ["Inter", "sans-serif"],
            "inter": ["Inter", "sans-serif"]
        },
        borderRadius: { "DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px" },
    },
    plugins: [],
};
