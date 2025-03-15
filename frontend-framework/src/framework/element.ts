import { h } from "snabbdom";
import { EventHandler } from "./event";

const initialState = {
  template: "",
  on: {},
};

function createReducer(args: (string | EventHandler)[]) {
  return (acc: typeof initialState, currentString: string, index: number) => {
    const currentArg = args[index];
    if (currentArg && currentArg.type === "event") {
      return { ...acc, on: { click: currentArg.click } };
    }
    return {
      ...acc,
      template: acc.template + currentString + (args[index] || ""),
    };
  };
}

type Tags = "div" | "p" | "button";

function createElement(tagName: Tags) {
  return (
    strings: TemplateStringsArray,
    ...args: (string | EventHandler)[]
  ) => {
    const { template, on } = strings.reduce(createReducer(args), initialState);
    return {
      type: "element",
      template: h(tagName, { on }, template),
    } as const;
  };
}

export const p = createElement("p");
export const div = createElement("div");
export const button = createElement("button");
