import { div } from "../framework/element";
import { onClick } from "./event";

export function User({
  firstName,
  lastName,
}: {
  firstName: string;
  lastName: string;
}) {
  return div`${onClick(() => alert(firstName))} Hello ${firstName} ${lastName}`;
}
