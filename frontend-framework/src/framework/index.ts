import * as snabbdom from "snabbdom";
const patch = snabbdom.init([snabbdom.eventListenersModule]);

export function init(
  selector: string,
  component: { template: snabbdom.VNode },
) {
  const app = document.querySelector(selector)!;
  patch(app, component.template);
}

export const createComponent =
  ({ template, methods = {}, initialState = {} }) =>
  (props) =>
    template(props);
