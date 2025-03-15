const createElement =
  (tagName: string) =>
  (strings: TemplateStringsArray, ...args: string[]) => ({
    type: tagName, // this will be useful for the next chapter
    template: strings.reduce(
      (acc, currentString, index) => acc + currentString + (args[index] || ""),
      "",
    ),
  });

const p = createElement("p");

const firstName = "Marvin";
const lastName = "Frachet";

const { template } = p`Hello ${firstName} ${lastName} !`;
console.log(template);
