# Custom Test-Center Heads Up Displays

This folder serves as an example of how to setup the source-code of a custom HUD that can be
loaded into TestCenter to provide iformation and interaction to the operator.

__Overview of Files__:

 - hud.js: The structure and logic of the HUD
 - hud.css: Styling and layout of HUD structure
 - jsconfig.json: A simple anchor file to help IDE (VSCode) recognize that this directory
                  is a Javascript project.
 - env.d.ts: A TypeScript typing file that defines the APIs provided by TestCenter
             to facilitate designing a HUD.


## Javascript API

### The Running Environment

`hud.js` is executed within a ES6 compatible Chromium browser context, and as such has `window` and `document` globals
avaiable.

`hud.js` is also executed within an effective Node.js v16+ environment. 
The builtin [Node.js API](https://nodejs.org/api/) is generally avaiable for use, including
`child_process`, `fs/promises`, etc.

There is no provision for multiple source-files at this point. So if you want to use ES6 imports or CommonJS require statements then you'll need a bundler like Rollup.js or Webpack to pre-process your project.

### The ATP Interface

TestCenter provides an `atp` object that provides a communications interface with your running subinitial.automation Python process.

You can find documentation on each method of the `atp` object in the first portion of `env.d.ts`.

Some common usage patterns for the `atp` object are:

1) Responding to data broadcasts coming from the ATP (Python).
2) Triggering Actions (in Python) as a response to some operator input.

### Mithril.js

TestCenter provides a slimmed down implementation of [Mitrhil.js](https://mithril.js.org/).
Mithril.js provides the tools for designing the HUD GUI copmonents.

The two main usage patterns for Mithril.js in this context is:

1) The `m(...)` hyperscript function call that creates HTML/DOM elements and strucure.
2) The `m.mount(...)` call that mounts the HTML/DOM elements as a [component](https://mithril.js.org/#components) which consisute your HUD.

The mithril.js.org examples & guide are good to read in order to understand `hud.js` better.
