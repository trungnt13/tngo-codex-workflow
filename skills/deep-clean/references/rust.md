# Rust Cleanup Rules

Use Rust's type system to remove invalid states, but do not hide domain control flow in unreadable chains.

Good cleanup targets:

```text
- unreachable branches and unused imports/items
- duplicated match arms with identical behavior
- repeated validation that belongs at a typed boundary
- needless clone/collect/to_string when ownership is already available
- simple `if let`, `matches!`, `?`, and Option/Result combinators when locally readable
```

Reject:

```text
- long combinator chains that hide branches or side effects
- new macros just to reduce line count
- generic traits/types before the repeated shape is stable
- public API expansion or changed error behavior
- removal of defensive checks without tests or type-level proof
```

Validation hints:

```text
cargo test --manifest-path <target Cargo.toml>
cargo clippy --all-targets --all-features --manifest-path <target Cargo.toml> -- -D warnings
cargo fmt --check --manifest-path <target Cargo.toml>
```

Use the project's existing cargo workspace/package shape.
