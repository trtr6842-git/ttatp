/* Custom Test-Center Heads-Up-Display (HUD) Example */
const fs = require("fs/promises")
let count = 0

let ls = await fs.readdir("/")

let HudComponent = {
  view() {
    return m("main", [
      m("h1", {class: "title"}, "Heads Up Display2"),
      m("button", {onclick: function() {
        count++
      }}, count + " clicks"),
      m("h2", "Directory Listing"),
      m("ul.filelist", ls.map((fname) => m("li", fname)))
    ])
  }
}

m.mount(atp.getHudRoot(), HudComponent)

function cleanup() {
  m.mount(atp.getHudRoot(), null)
}

return cleanup
