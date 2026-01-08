'use client'
import React from 'react'
import CountUp from 'react-countup';

let data = [
    {
        title:'Active Jobs',
        value:200,
        symbol:'M'
    },
    {
        title:'Startups',
        value:40,
        symbol:'K'
    },
    {
        title:'Talents',
        value:340,
        symbol:'K'
    },
]
interface Data{
    title: string;
    value: number;
    symbol: string;
}

export default function HomeBannerCounter() {
  return (
        <ul>
            {data.map((item:Data,index:number)=>( 
                <li key={index}>
                    <div className="lios-parts">
                        <h2><span className="ctr"><CountUp end={item.value} /></span><span className="text-main">{item.symbol}</span></h2>
                        <h6>{item.title}</h6>
                    </div>
                </li>
            ))}
        </ul>
  )
}
