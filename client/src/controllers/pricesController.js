import moment from "moment";

const url =
  "http://stocks-prediction-backend.eba-jf2rqnk2.me-south-1.elasticbeanstalk.com";

const formatDate = (date) => moment(date).format("MMMM D YYYY");

export const get_prices = async (symbol) => {
  const res = await fetch(`${url}/prices/${symbol}`);
  const body = await res.json();
  let { prices, predictions } = body;

  prices = prices.map((p) => ({
    ...p,
    date: formatDate(p.date),
  }));

  prices.sort((a, b) => new Date(a.date) - new Date(b.date));


  predictions = predictions.map((p) => ({
    prediction: p.close,
    date: formatDate(p.date),
    
  }));

  predictions.sort((a, b) => new Date(a.date) - new Date(b.date));

  const { stock } = body;

  return { prices, stock, predictions };
};

export const get_predictions = async (symbol) => {
  const res = await fetch(`${url}/predict/${symbol}`);
  const body = await res.json();

  let predictions = body.predictions;
  predictions = predictions.map((p) => ({
    prediction: p.close,
    date: formatDate(p.date),
  }));
  delete predictions.close;
  console.log({ predictions });
  return predictions;
};
