export const onClick = (f: () => void) => ({
  type: "event",
  click: f,
});
