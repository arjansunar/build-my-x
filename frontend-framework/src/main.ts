import { init } from "./framework";
import { div } from "./framework/element";

const firstName = "Arjan";
const lastName = "Sunar";

init("#app", div`Hello ${firstName} ${lastName}`);
