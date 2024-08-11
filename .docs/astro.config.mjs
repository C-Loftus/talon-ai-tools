import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
    site: "https://colton.place/talon-ai-tools",
    base: "talon-ai-tools",
    integrations: [
        starlight({
            title: "talon-ai-tools Docs",
            social: {
                github: "https://github.com/C-Loftus/talon-ai-tools",
            },
            sidebar: [
                {
                    label: "Guides",
                    autogenerate: { directory: "guides" },
                },
                {
                    label: "Reference",
                    autogenerate: { directory: "reference" },
                },
            ],
        }),
    ],
});
