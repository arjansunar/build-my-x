class Promisible {
  private promiseChain: ((value: unknown) => unknown)[];
  private handleError: (error: unknown) => void;
  constructor(
    execFn: (
      onResolve: (value: unknown) => void,
      onReject: (value: unknown) => void,
    ) => void,
  ) {
    this.promiseChain = [];
    this.handleError = () => {};
    this.onResolve = this.onResolve.bind(this);
    this.onReject = this.onReject.bind(this);
    execFn(this.onResolve, this.onReject);
  }

  then(handleSuccess) {
    this.promiseChain.push(handleSuccess);
    return this;
  }
  catch(handleError) {
    this.handleError = handleError;
    return this;
  }

  onResolve(value) {
    let stored = value;

    try {
      this.promiseChain.forEach((nextFn) => {
        stored = nextFn(value);
      });
    } catch (error) {
      this.promiseChain = [];
      this.onReject(error);
    }
  }
  onReject(error) {
    this.handleError(error);
  }
}

function simulatedNetworkFetch() {
  const data = {
    id: 10,
    name: "Testing user",
  } as const;

  if (Math.random() > 0.05) {
    return {
      data,
      statusCode: 200,
    };
  } else {
    const error = {
      statusCode: 404,
      message: "Could not find user",
      error: "Not Found",
    };

    return error;
  }
}

function apiHandler() {
  return new Promisible((onResolve, onReject) => {
    setTimeout(() => {
      const res = simulatedNetworkFetch();
      if (res.statusCode >= 400) {
        onReject(res);
      } else {
        onResolve(res.data);
      }
    }, 3000);
  });
}

function main() {
  console.log("Hey...");
  apiHandler()
    .then((data) => console.log("Data is:", data))
    .catch((err) => console.error("Error: ", err));
  console.log("Should be executed immediately after");
}

main();
