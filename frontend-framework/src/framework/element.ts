const createElement =
  (tagName: string) =>
  (strings: TemplateStringsArray, ...args: string[]) => ({
    type: tagName, // this will be useful for the next chapter
    template: strings.reduce(
      (acc, currentString, index) => acc + currentString + (args[index] || ""),
      "",
    ),
  });

export const p = createElement("p");
export const div = createElement("div");
