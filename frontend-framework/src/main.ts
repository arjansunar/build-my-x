import { init } from "./framework";
import { User } from "./framework/user";

const firstName = "Arjan";
const lastName = "Sunar";

init("#app", User({ firstName, lastName }));
