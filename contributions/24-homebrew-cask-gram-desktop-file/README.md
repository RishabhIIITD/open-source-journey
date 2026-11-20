# Case Study 24: Homebrew Cask — Linux XDG Desktop Entry & Icon Integration for Gram

> **Target Repository**: [Homebrew/homebrew-cask](https://github.com/Homebrew/homebrew-cask)  
> **Upstream PR**: [#304572](https://github.com/Homebrew/homebrew-cask/pull/304572)  
> **Linked Issue**: [#303878](https://github.com/Homebrew/homebrew-cask/issues/303878)  
> **Component**: `Casks/g/gram.rb`  
> **Contributor**: Rishabh Bafna ([@RishabhIIITD](https://github.com/RishabhIIITD))  
> **Technologies**: Ruby, Homebrew Cask DSL, XDG Desktop Entry Spec, FreeDesktop Icons, RuboCop  

---

## 1. Executive Summary

[Gram](https://gram-editor.com/) is a high-performance open-source text editor built on Rust (derived from Zed). In [Homebrew Cask](https://github.com/Homebrew/homebrew-cask), the `gram` cask distributes cross-platform binaries for macOS (universal DMG) and Linux (aarch64 and x86_64 tarball distributions).

On Linux, installing Gram previously linked only the command-line launcher via `binary "#{staged_path}/gram.app/bin/gram"`. However, desktop environments (GNOME, KDE Plasma, XFCE, Sway) require a valid `.desktop` file located in `~/.local/share/applications/` and scalable vector icons in the FreeDesktop icon path to index GUI applications. Because these assets were omitted from the cask artifact stanzas, users who installed Gram via Homebrew on Linux could run `gram` from the terminal, but the editor was completely invisible in application launchers, dock menus, and system file association managers ([Issue #303878](https://github.com/Homebrew/homebrew-cask/issues/303878)).

This contribution resolves the issue by adding an `artifact` stanza for `app.liten.Gram.desktop`, configuring dynamic `preflight_steps` to rewrite the `Exec` and `Icon` directives to absolute Homebrew installation targets, cleaning up cask stanza style rules, and updating `zap trash` paths.

---

## 2. Problem & Root Cause Analysis

### The Flawed Cask Definition
In `Casks/g/gram.rb` (prior to PR #304572):
```ruby
on_linux do
  binary "#{staged_path}/gram.app/bin/gram"

  zap trash: [
    "~/.cache/gram",
    "~/.config/gram",
    "~/.local/share/gram",
  ]
end
```

### The Architectural Discrepancy
Unlike AppImage distributions (such as Audacity) where Homebrew's `app_image` DSL extracts metadata automatically, Gram's Linux release is a compressed directory hierarchy containing:
```text
gram.app/
├── bin/
│   └── gram
├── share/
│   ├── applications/
│   │   └── app.liten.Gram.desktop
│   └── icons/hicolor/
│       ├── scalable/apps/app.liten.Gram.svg
│       └── symbolic/apps/app.liten.Gram-symbolic.svg
└── libexec/
    └── gram-editor
```

Inside the raw `app.liten.Gram.desktop` file:
```ini
[Desktop Entry]
Name=Gram
TryExec=gram
Exec=gram %U
Icon=app.liten.Gram
Categories=Development;TextEditor;IDE;
```

Without an explicit `artifact` stanza linking `app.liten.Gram.desktop` to `~/.local/share/applications/`, desktop application launchers ignore the staged files. Furthermore:
1. `Exec=gram %U` depends on whether the user's GUI session inherited the Homebrew shell environment `$PATH`.
2. `Icon=app.liten.Gram` fails to load unless resolved to the bundled SVG icon in the staged directory.

---

## 3. The Solution

Following the established reference pattern in `zed.rb`:

```ruby
on_linux do
  binary "gram.app/bin/gram"
  artifact "gram.app/share/applications/app.liten.Gram.desktop",
           target: "~/.local/share/applications/app.liten.Gram.desktop"

  preflight_steps do
    inreplace "gram.app/share/applications/app.liten.Gram.desktop", "Exec=gram",
              "Exec={{HOMEBREW_PREFIX}}/bin/gram"
    inreplace "gram.app/share/applications/app.liten.Gram.desktop", "Icon=app.liten.Gram",
              "Icon={{staged_path}}/gram.app/share/icons/hicolor/scalable/apps/app.liten.Gram.svg"
  end

  zap trash: [
    "~/.cache/gram",
    "~/.config/gram",
    "~/.local/share/applications/app.liten.Gram.desktop",
    "~/.local/share/gram",
  ]
end
```

### Key Engineering Decisions
1. **Dynamic Path Templating**: Using `{{HOMEBREW_PREFIX}}` and `{{staged_path}}` ensures the desktop file references the exact architecture prefix (`/home/linuxbrew/.linuxbrew` on Linux) regardless of custom installation prefixes.
2. **Icon Resolution**: Rewriting `Icon` to the persistent SVG path in `{{staged_path}}` avoids polluting system icon caches while guaranteeing rendering in HiDPI desktop environments.
3. **Cleaned Binary Stanza**: Replaced the redundant `#{staged_path}` interpolation with clean relative path `gram.app/bin/gram` compliant with Homebrew rubocop cops.

---

## 4. Verification & Testing

- `brew style --cask gram`: Inspected 1 file, 0 offenses detected.
- `brew audit --cask --online gram`: Verified download integrity, checksums, and metadata compliance. Zero errors.
- Template conformance verified through Homebrew's automated `check-prs.yml` gate.
