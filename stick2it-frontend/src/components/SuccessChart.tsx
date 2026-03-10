"use client"

import { TrendingUp } from "lucide-react"
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

export const description = "A linear area chart"

const chartData = [
  { month: "January", completions: 30 },
  { month: "February", completions: 21 },
  { month: "March", completions: 34 },
  { month: "April", completions: 45 },
  { month: "May", completions: 20 },
  { month: "June", completions: 25 },
]

const chartConfig = {
  completions: {
    label: "Completion",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig

export function SuccessChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Success Rate over Time</CardTitle>
        <CardDescription>
          Showing total completions for the last 6 months
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-72 w-full">
          <AreaChart
            accessibilityLayer
            data={chartData}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value:any) => value.slice(0, 3)}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="dot" hideLabel />}
            />
            <Area
              dataKey="completions"
              type="linear"
              fill="#F0EFFF"
              fillOpacity={0.9}
              stroke="#F0EFFF"
            />
          </AreaChart>
        </ChartContainer>
      </CardContent>
      <CardFooter>
        <div className="flex w-full items-start gap-2 text-sm">
          <div className="grid gap-2">
            <div className="flex items-center gap-2 leading-none font-medium">
              Up by 5.2% this month <TrendingUp className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-2 leading-none text-muted-foreground">
              January - June 2026
            </div>
          </div>
        </div>
      </CardFooter>
    </Card>
  )
}
