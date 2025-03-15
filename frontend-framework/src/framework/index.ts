import * as snabbdom from "snabbdom";
const patch = snabbdom.init([snabbdom.eventListenersModule]);

type Component = {
  type: "element" | "event";
  template: snabbdom.VNode;
};

export function init(selector: string, component: Component) {
  const app = document.querySelector(selector)!;
  patch(app, component.template);
}

let state = {};
export function createComponent({
  template,
  methods = {},
  initialState = {},
}: {
  template: (...args: any[]) => Component;
  methods: Record<string, (...args: any[]) => any>;
  initialState: Record<string, any>;
}) {
  state = initialState;

  let previous: Component;
  // provides default state for the various components
  const mappedMethods = (props: typeof initialState) =>
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
  return (props?: typeof initialState) => {
    previous = template({
      ...(props ?? initialState),
      methods: mappedMethods(props),
    });
    return previous;
  };
}
