# Multipage example

```bash
streamlit run examples/multipage/app.py
```

This example demonstrates the multipage API around `Router`:

- `App()(Router(...)(Page(...), Page(...)))` declares the whole multipage app as a single root tree.
- `Router` contains only `Page` children and is responsible for wiring `st.navigation(...)`.
- `Page(...)(OverviewPage(key="root"))` declares an inline page from an instantiated component.
- `Page(...)("pages/report_page.py")` declares a file-backed page that Streamlit executes directly.
- `App(page_title=..., page_icon=..., layout=...)` configures the shared web page envelope for the app.
- `nav_title` and `nav_icon` configure the navigation label and icon for each page.
- `app.shared_state("workspace", WorkspaceState())` declares the global shared state in one central place.
- `WorkspaceSidebar` is a normal reusable component rendered by each page inside `sidebar(...)`.
- `get_shared_state("workspace")` is then used for consumption inside page components and the shared sidebar.

What to try:

1. Edit the sidebar fields on the overview page.
2. Switch to the report page and verify that the sidebar kept the same values.
3. Increment the shared visits counter from the sidebar on one page.
4. Switch pages and verify that the updated value followed you.
5. Edit the local note field on each page and switch back and forth.

Files:

- `examples/multipage/app.py`: entrypoint, router, and inline page.
- `examples/multipage/pages/report_page.py`: file-backed page.
- `examples/multipage/shared.py`: shared state schema and reusable sidebar component used by both pages.
