import React from "react";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import { get_predictions, get_prices } from "../controllers/pricesController";

function CompanyPage() {
	const [prices, setPrices] = useState(null);
	const [predictions, setPredictions] = useState(null)
	const [data, setData] = useState(null)
	const [stock, setStock] = useState(null);
	const { symbol } = useParams()

  useEffect(() => {
    if (!prices) {
			get_prices(symbol).then(({prices, stock, predictions}) => {
				setPrices(prices)
				setStock(stock)
				setPredictions(predictions)
				setData([...prices.slice(-20, -1), ...predictions])
			});
		}
		console.log({ data })
  }, [data, prices, predictions, symbol]);
  return (
    <div>
			<header>
				<h1>{stock && stock.company_name}</h1>
			</header>
      {prices && (
				<LineChart compact={true} defaultShowTooltip={true} width={1200} height={400} data={data}>
					<Line type="monotone" dataKey="close" stroke="#8884d8" />
					{predictions && 
						<Line type="monotone" dataKey="prediction" stroke="#bd84d8" />
					}
          <Tooltip />
          <XAxis dataKey="date" />
          <YAxis />
        </LineChart>
      )}
    </div>
  );
}

export default CompanyPage;
