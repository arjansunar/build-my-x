export type EventHandler = {
  type: "event";
};

export const onClick = (f: () => void) =>
  ({
    type: "event",
    click: f,
  }) as const;
