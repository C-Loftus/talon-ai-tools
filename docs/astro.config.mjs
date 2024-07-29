import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
    site: "https://colton.place/talon-ai-tools",
    base: "/",
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
                        { label: "Quickstart", slug: "guides/quickstart" },
                        { label: "Customizing", slug: "guides/customizing"}
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
