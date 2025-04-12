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
export function createComponent<const S extends Record<string, any>>({
  template,
  methods = {},
  initialState = {} as S,
}: {
  template: (...args: any[]) => Component;
  methods: Record<string, (...args: any[]) => any>;
  initialState: S;
}) {
  state = initialState;

  let previous: Component;
  // provides default state for the various components
  const mappedMethods = (props: typeof initialState) => {
    return Object.keys(methods).reduce(
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
  };
  return (props?: typeof initialState) => {
    let _props = props ?? initialState;
    if (!!props) {
      state = _props;
    }
    previous = template({
      ..._props,
      methods: mappedMethods(_props),
    });
    return previous;
  };
}
