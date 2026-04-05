def body_or_prop(element):
    return element.children[0] if element.children else element.props.get("body", "")
