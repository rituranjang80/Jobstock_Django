import React from 'react'
import Link from 'next/link'
import { categoryData } from '../../data/data'

interface Category{
    icon: string;
    title: string;
    job: string;
}

export default function CategoryTwo({border}:{border:boolean}) {
  return (
        <div className="row justify-content-center gx-4 gy-4">
            {categoryData.map((item:Category,index:number)=>( 
                <div className="col-xl-3 col-lg-3 col-md-4 col-sm-6" key={index}>
                    <div className={`card  py-4 px-4 rounded-4 mb-0 ${border ? 'border' : 'border-0'}`}>
                        <div className="ctrd-icons mb-3">
                            <i className={`text-main fs-1 ${item.icon}`}></i>
                        </div>
                        <div className="ctrd-caps">
                            <h4 className="fs-5"><Link href="/advance-search">{item.title}</Link></h4>
                            <p className="mb-3">You can view all popular jobs according your future careers.</p>
                            <p className="text-main fw-medium mb-0">{item.job}</p>
                        </div>
                    </div>
                </div>
            ))}
        </div>
  )
}
