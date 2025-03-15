import * as snabbdom from "snabbdom";
const patch = snabbdom.init([]);

export function init(
  selector: string,
  component: { template: snabbdom.VNode },
) {
  const app = document.querySelector(selector)!;
  patch(app, component.template);
}
