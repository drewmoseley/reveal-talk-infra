# reveal-talk-infra — Claude guidance

This directory is shared infrastructure for Reveal.js slide decks authored in
Pandoc Markdown.  It is included in each talk repo as `infra/` (git submodule
or copy).

---

## System overview

```
<talk-repo>/
  Makefile          # defines talk vars, then: include $(INFRA_DIR)/Makefile.include
  sections/         # NNN-slug.md slide files (three-digit prefix, sorted)
  img/              # images referenced from slides
  talk-extras.css   # talk-specific CSS loaded after infra/custom.css
  infra/            # this repo (symlink or submodule)
    Makefile.include
    revealjs-template.html
    custom.css
    manage_slides.py
    vendor/reveal.js/
  build/            # generated output (not committed)
```

---

## Setting up a new talk

1. Add this repo as `infra/` (submodule: `git submodule add <url> infra`).
2. Create `Makefile` with at minimum:

```makefile
BUILD_DIR   := build
HTML_OUT    := $(BUILD_DIR)/my-talk.html
PDF_OUT     := $(BUILD_DIR)/my-talk.pdf
ORG_OUT     := $(BUILD_DIR)/my-talk.org
TITLE_LOGOS := img/logo1.png img/logo2.png   # space-separated, shown on title slide
EXTRA_CSS   := talk-extras.css               # omit if no extra styles
INFRA_DIR   := infra
include $(INFRA_DIR)/Makefile.include
```

Optional Makefile overrides (before the include):

| Variable           | Default       | Purpose                            |
|--------------------|---------------|------------------------------------|
| `SLIDES_DIR`       | `sections`    | where NNN-slug.md files live       |
| `REVEAL_WIDTH`     | `1920`        | slide canvas width                 |
| `REVEAL_HEIGHT`    | `1080`        | slide canvas height                |
| `REVEAL_TRANSITION`| `fade`        | reveal.js transition               |
| `REVEAL_TEMPLATE`  | infra template| pandoc HTML template               |
| `CUSTOM_CSS`       | `infra/custom.css` | base CSS                      |

3. Create `sections/001-intro.md` (see slide format below).
4. Add `talk-extras.css` for talk-specific overrides.
5. Run `make` to build.

---

## Build commands

```sh
make            # build both HTML and Org output
make reveal     # build reveal.js HTML only → build/<name>.html
make org        # build Org mode only → build/<name>.org
make pdf        # build PDF via decktape (requires npx)
make clean      # remove build/
```

Open `build/<name>.html` directly in a browser (no server needed for local
preview; PDF export needs a local HTTP server, handled by `make pdf`).

---

## Slide file format

### Naming

Files are named `NNN-slug.md` (three-digit zero-padded prefix).  `make` sorts
them numerically and concatenates before passing to pandoc.

### Title / metadata block (first file only)

```markdown
% Talk Title; Optional Subtitle
% <img src="img/headshot.png"> Speaker Name, Role, Company
% Conference Name – Month DD, YYYY
```

The `%` lines become pandoc title, author, and date metadata.  HTML in the
author line is passed through to the title slide template.

### Slide separator

`---` (horizontal rule) on its own line starts a new slide.

### Slide heading

`## Slide Title` — H2 is the slide title (pandoc `-V slide-level=2`).

H1 would be a section/chapter divider creating a vertical slide group (rarely
used).  H3 is a sub-heading within a slide body.

### Pandoc fenced divs (for CSS classes)

```markdown
:::: {.slide-columns}
::: {.slide-col-left}
Left content
:::
::: {.slide-col-right}
Right content
:::
::::
```

Nested fenced divs: add one more `:` per nesting level.

### Reveal.js fragments (appear on click)

```markdown
- item one
- item two {.fragment}

<p class="fragment">Paragraph that appears on click.</p>

<div class="fragment">Any block.</div>
```

Or on a whole bullet list, add `{.fragment}` to each `- item`.

### Speaker notes

```markdown
::: notes
These notes appear in the presenter view (press S).
:::
```

### Raw HTML in slides

Inline HTML passes through pandoc directly.  Use for complex layouts not
expressible in Markdown.

---

## CSS classes — infra/custom.css

### Slide type modifiers (on the H2)

| Class              | Usage                        | Effect                          |
|--------------------|------------------------------|---------------------------------|
| `.section-divider` | `## DEMO TIME! {.section-divider}` | Dark blue background, white text, large heading |
| `.speaker-slide`   | `## WITH YOU TODAY… {.speaker-slide}` | Speaker bio layout          |

### Layout components

| Class / element                   | Description                              |
|-----------------------------------|------------------------------------------|
| `.tool-logos` div                 | Horizontal row of tool logos (48 px tall)|
| `.right-logos` div                | 5-logo pentagon panel on right side      |
| `.slide-footnote` p               | Small footnote pinned to slide bottom    |

### right-logos pentagon layout

```html
<div class="right-logos">
  <img src="img/logo1.svg" title="Tool 1">  <!-- top -->
  <img src="img/logo2.svg" title="Tool 2">  <!-- upper-right -->
  <img src="img/logo3.svg" title="Tool 3">  <!-- lower-right -->
  <img src="img/logo4.svg" title="Tool 4">  <!-- lower-left -->
  <img src="img/logo5.svg" title="Tool 5">  <!-- upper-left -->
</div>
```

Supports exactly 5 images; add matching `:nth-child` rules in `custom.css` for
other counts.

---

## manage_slides.py

Run from the **repo root** (not from `infra/`).

```sh
# Insert a new slide at position 4 (shifts 4+ up by 1)
python3 infra/manage_slides.py insert 4 "Multi-arch builds"

# Delete the slide at position 7 (shifts 8+ down by 1, asks for confirmation)
python3 infra/manage_slides.py delete 7
```

The script rewrites filenames to keep prefixes contiguous.  It does not touch
slide content.

---

## Theming notes

`custom.css` uses a Toradex-flavored palette:

| CSS variable        | Value     | Used for                      |
|---------------------|-----------|-------------------------------|
| `--toradex-blue`    | `#003b64` | headings, borders, key text   |
| `--toradex-green`   | `#8dc63f` | accent lines, port rows       |
| `--toradex-grey`    | `#f5f5f5` | light backgrounds             |

Main content slides use `img/main-slide-background.png` as a full-bleed
background (baked into infra/custom.css).  The title slide uses
`img/title-slide-background.png`.  Both images live in the **talk repo's**
`img/` directory (not in infra).

Talk-specific CSS overrides go in `talk-extras.css`, loaded after `custom.css`
via pandoc `-c` flags set in `Makefile.include` when `EXTRA_CSS` is defined.
