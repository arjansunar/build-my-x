import { createComponent } from ".";
import { div } from "../framework/element";
import { onClick } from "./event";

const initialState = { count: 0 };

const methods = {
  increament: (state: typeof initialState) => ({
    ...state,
    count: state.count + 1,
  }),
} as const;
type Method = typeof methods;

function template({
  count,
  methods,
}: typeof initialState & { methods: Method }) {
  // @ts-expect-error state is populated by our `framework`
  return div`${onClick(() => methods.increament())} Count is: ${count.toString()}`;
}

export const Counter = createComponent({
  template,
  methods,
  initialState,
});
