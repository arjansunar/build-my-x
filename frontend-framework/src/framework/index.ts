import * as snabbdom from "snabbdom";
const patch = snabbdom.init([snabbdom.eventListenersModule]);

export function init(
  selector: string,
  component: { template: snabbdom.VNode },
) {
  const app = document.querySelector(selector)!;
  patch(app, component.template);
}

let state = {};
export function createComponent({ template, methods = {}, initialState = {} }) {
  state = initialState;

  let previous;
  // provides default state for the various components
  const mappedMethods = (props) =>
    Object.keys(methods).reduce(
      (acc, key) => ({
        ...acc,
        [key]: (...args) => {
          // update to data using method
          state = methods[key](state, ...args);
          // create new template with updated data
          const nextNode = template({
            ...props,
            ...state,
            methods: mappedMethods(props),
          });
          patch(previous.template, nextNode.template);
          previous = nextNode;
          return state;
        },
      }),
      {},
    );
  return (props) => {
    previous = template({ ...props, methods: mappedMethods(props) });
    return previous;
  };
}
