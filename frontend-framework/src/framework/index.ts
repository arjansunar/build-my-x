export function init(selector: string, component) {
  const app = document.querySelector(selector);
  const newElement = document.createElement(component.type);
  const newTextComponent = document.createTextNode(component.template);

  newElement.appendChild(newTextComponent);
  app?.append(newElement);
}
