import { div } from "../framework/element";

export function User({
  firstName,
  lastName,
}: {
  firstName: string;
  lastName: string;
}) {
  return div`Hello ${firstName} ${lastName}`;
}
