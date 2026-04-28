# Multipage example

```bash
streamlit run examples/16_multipage/app.py
```

This example demonstrates the multipage API around `Router`:

- `App(Router(...)(Page(...), Page(...)))` declares the whole multipage app as a single root tree.
- `Router` contains only `Page` children and is responsible for wiring `st.navigation(...)`.
- `Router(chrome=AppChrome)` declares a chrome wrapper class — the framework instantiates it around every active page (inline and file-backed), and the page renders where the chrome places `*self.children`. Path: `app.router.chrome.<page>.<source>` — chrome's own fiber lives at `app.router.chrome`, page-independent, so chrome state survives navigation.
- `Page(...)(OverviewPage(key="root"))` declares an inline page from an instantiated component.
- `Page(...)("pages/report_page.py")` declares a file-backed page that Streamlit executes directly. It still renders inside the Router's chrome via `get_app().render_page(...)`.
- a lightweight `Provider` is mounted above the router so both pages, including the file-backed one, can read the same ambient context.
- `App(page_title=..., page_icon=..., layout=...)` configures the shared web page envelope for the app.
- `nav_title` and `nav_icon` configure the navigation label and icon for each page.
- `app.create_shared_state("workspace", WorkspaceState())` declares the global shared state in one central place — it is what keeps the sidebar inputs in sync across navigation (chrome state itself is per-page).
- `WorkspaceSidebar` is the reusable component instantiated once inside `AppChrome`, not in each page.
- `get_shared_state("workspace")` is consumed inside the sidebar and the page bodies.

What to try:

1. Edit the sidebar fields on the overview page.
2. Switch to the report page and verify that the sidebar kept the same values (driven by the shared state, not by the chrome fiber).
3. Increment the shared visits counter from the sidebar on one page.
4. Switch pages and verify that the updated value followed you.
5. Edit the local note field on each page and switch back and forth — page-local state persists per page (its fiber lives at `app.router.chrome.<page>.root...`).

Files:

- `examples/16_multipage/app.py`: entrypoint, router, chrome, and inline page.
- `examples/16_multipage/pages/report_page.py`: file-backed page.
- `examples/16_multipage/shared.py`: shared state schema, sidebar component, and `AppChrome` wrapper.
