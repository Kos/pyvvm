# What's this?

A library designed to help with Model-View-ViewModel programming in Python. Provides helpers to easily write nice models (especially view-models) that can be automatically hooked up into UI (with two-side data binding) with no redundant glue code.

# What comes in the box?

- A spec for the extended property interface.
- A flexible implementation thereof, likely to cover your scenario.
- UI data binding code for PySide (Qt) that uses the interface.
- Examples

# Status

WIP. The thing is written and field-tested inside a larger project; I'm extracting, refactoring and documenting.

# Tests

Yes.

# FAQ

- Can I make my own implementation for the property interface?
  - Yup. Go ahead if the provided doesn't suit you.
- Can I use standard Python properties or methods in my models?
  - Yup.
- And regular fields?
  - Hmm.
- Can I use any UI toolkit?
  - Yes, I think so. Write the part that connects the UI to the view-models.

