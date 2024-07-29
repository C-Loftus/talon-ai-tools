import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
    site: "https://colton.place/",
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
                    items: [
                        // Each item here is one entry in the navigation menu.
                        { label: "Example Guide", slug: "guides/example" },
                    ],
                },
                {
                    label: "Reference",
                    autogenerate: { directory: "reference" },
                },
            ],
        }),
    ],
});
