import Image from 'next/image'
import React from 'react'

let images = [
    '/img/brand/layar-primary.svg',
    '/img/brand/mailchimp-primary.svg',
    '/img/brand/fitbit-primary.svg',
    '/img/brand/capsule-primary.svg',
    '/img/brand/vidados-primary.svg',
]

export default function PartnerOne() {
  return (
        <div className="row align-items-center justify-content-center row-cols-xl-5 row-cols-lg-5 row-cols-md-3 row-cols-3 gx-3 gy-3">
            {images.map((item:string,index:number)=>( 
                <div className="col" key={index}>
                    <figure className="single-brand thumb-figure" key={index}>
                        <Image src={item} width={0} height={0} sizes='100vw' style={{width:'auto', height:'60px'}} className="img-fluid" alt=""/>
                    </figure>
                </div>
            ))}
        </div>
  )
}
