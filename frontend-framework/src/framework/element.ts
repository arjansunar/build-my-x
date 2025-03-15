import { h } from "snabbdom";

const initialState = {
  template: "",
};

function createReducer(args: string[]) {
  return (acc: typeof initialState, currentString: string, index: number) => ({
    ...acc,
    template: acc.template + currentString + (args[index] || ""),
  });
}

function createElement(tagName: string) {
  return (strings: TemplateStringsArray, ...args: string[]) => {
    const { template } = strings.reduce(createReducer(args), initialState);
    return {
      type: "element",
      template: h(tagName, {}, template),
    };
  };
}

export const p = createElement("p");
export const div = createElement("div");
