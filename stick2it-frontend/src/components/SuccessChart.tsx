"use client"

import { TrendingUp } from "lucide-react"
import { Area, AreaChart, CartesianGrid, XAxis, ResponsiveContainer } from "recharts"
import { useMemo, useState } from "react"
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
import { Skeleton } from "@/components/ui/skeleton";
import {useTasks} from "../context/TaskContext"
import { Button } from "@/components/ui/button"

type TimeRange = "7d" | "1m" | "3m";

export const description = "A linear area chart"

export function SuccessChart() {
  const { commitments, loading } = useTasks();
  const [timeRange, setTimeRange] = useState<TimeRange>("7d");

  const dynamicData = useMemo(() => {
    const now = new Date();
    let daysToScroll: number;

    // Determine range
    if (timeRange === "7d") daysToScroll = 7;
    else if (timeRange === "1m") daysToScroll = 30;
    else daysToScroll = 90;

    const dataMap: Record<string, number> = {};

    // Initialize the range with 0s so the chart doesn't have gaps
    for (let i = daysToScroll - 1; i >= 0; i--) {
      const d = new Date();
      d.setDate(now.getDate() - i);
      const label = timeRange === "7d" 
        ? d.toLocaleDateString(undefined, { weekday: 'short' }) 
        : d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      dataMap[label] = 0;
    }

    // Aggregate real data
    commitments.forEach((c) => {
      if (c.status === 'completed' && c.date) {
        const cDate = new Date(c.date);
        const diffDays = (now.getTime() - cDate.getTime()) / (1000 * 3600 * 24);

        if (diffDays <= daysToScroll) {
          const label = timeRange === "7d" 
            ? cDate.toLocaleDateString(undefined, { weekday: 'short' }) 
            : cDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
          if (dataMap.hasOwnProperty(label)) dataMap[label]++;
        }
      }
    });

    return Object.entries(dataMap).map(([label, completions]) => ({
      label,
      completions
    }));
  }, [commitments, timeRange]);

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-2xl shadow-sm border border-gray-100">
        <Skeleton className="h-6 w-32 mb-8" /> {/* Chart Title */}
        <div className="flex items-end justify-between h-48 gap-2">
          {/* Generate 7 bars for the week */}
          {[...Array(7)].map((_, i) => (
            <Skeleton 
              key={i} 
              className="w-full" 
              style={{ height: `${Math.floor(Math.random() * 60) + 40}%` }} 
            />
          ))}
        </div>
        <div className="flex justify-between mt-4">
          {[...Array(7)].map((_, i) => (
            <Skeleton key={i} className="h-3 w-8" />
          ))}
        </div>
      </div>
    );
  }
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <div>
          <CardTitle>Success Rate</CardTitle>
          <CardDescription>Visualizing your recent completions</CardDescription>
        </div>
        {/* 🌟 View Switcher Tabs */}
        <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-lg">
          {(["7d", "1m", "3m"] as TimeRange[]).map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? "default" : "ghost"}
              size="sm"
              className={`text-xs h-7 px-3 ${timeRange === range ? "shadow-sm" : ""}`}
              onClick={() => setTimeRange(range)}
            >
              {range.toUpperCase()}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer config={{ completions: { label: "Completions", color: "#6366F1" } }} className="h-64 w-full">          
          <AreaChart
            accessibilityLayer
            data={dynamicData}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="#f0f0f0"/>
            <XAxis
              dataKey="label"
              tickLine={false}
              axisLine={false}
              tickMargin={10}
              tickFormatter={(value:any) => value.slice(0, 3)}
              className="text-[10px] md:text-xs"
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent indicator="line" hideLabel />}
            />
            <Area
              type="monotone"
              dataKey="completions"
              stroke="#6366F1"
              strokeWidth={2}
              fill="url(#colorGradient)"
            />
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
              </linearGradient>
            </defs>
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
