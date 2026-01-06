'use client'
import React from 'react'
import Image from 'next/image';
import dynamic from 'next/dynamic';

const Select = dynamic(()=>import('react-select'),{ssr:false})

import { category, jobType, lavel, experience, sallary} from '../../data/select-option';

export default function FormOne() {
    return (
        <div className="hero-search-content verticle-space">
            <div className="row">
                <div className="col-xl-12 col-lg-12 col-md-12 col-sm-12">
                    <div className="form-group">
                        <div className="input-with-icon">
                            <input type="text" className="form-control border" placeholder="Search Job Keywords.."/>
                            <Image src='/img/pin.svg' width={18} height={18} alt=""/>
                        </div>
                    </div>
                </div>
            
                <div className="col-xl-6 col-lg-12 col-md-6 col-sm-6">
                    <div className="form-group">
                        <label className='mb-2'>Job Category</label>
                        <Select options={category}  className="form-control" placeholder="Software & Application"/>
                    </div>
                </div>
                <div className="col-xl-6 col-lg-12 col-md-6 col-sm-6">
                    <div className="form-group">
                        <label className='mb-2'>Job Type</label>
                        <Select options={jobType}  className="form-control" placeholder="All Type"/>
                    </div>
                </div>
                
                <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                    <div className="form-group">
                        <label className='mb-2'>Job Lavel</label>
                        <Select options={lavel}  className="form-control" placeholder="Junior Lavel"/>
                    </div>
                </div>
                <div className="col-xl-6 col-lg-6 col-md-6 col-sm-6">
                    <div className="form-group">
                        <label className='mb-2'>Experience</label>
                        <Select options={experience}  className="form-control" placeholder="1 Year"/>
                    </div>
                </div>
                
                <div className="col-xl-12 col-lg-12 col-md-12 col-sm-12">
                    <div className="form-group">
                        <label className='mb-2'>Expected Sallary</label>
                        <Select options={sallary}  className="form-control" placeholder="1 Year"/>
                    </div>
                </div>
                
                <div className="col-xl-12 col-lg-12 col-md-12 col-sm-12">
                    <button type="submit" className="btn btn-main full-width">Search Result</button>
                </div>
            </div>
        </div>
  )
}
