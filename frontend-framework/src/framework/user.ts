import { createComponent } from ".";
import { div } from "../framework/element";
import { onClick } from "./event";

const initialState = { firstName: "John", lastName: "Doe" };

const methods = {
  changeName: (state: typeof initialState, firstName: string) => ({
    ...state,
    firstName,
  }),
};

function template({
  firstName,
  lastName,
  methods,
}: {
  firstName: string;
  lastName: string;
}) {
  return div`${onClick(() =>
    methods.changeName("Thomas"),
  )} Hello ${firstName} ${lastName}`;
}

export const User = createComponent({
  template,
  methods,
  initialState,
});
