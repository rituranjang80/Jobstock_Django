import React from 'react'
import NavBgWhite from '../components/navbar/nav-bg-white'
import PricingOne from '../components/pricing/pricing-one'
import FooterTopTwo from '../components/footer/footer-top-two'
import FooterLightTwo from '../components/footer/footer-light-two'
import ScrollToTop from '../components/scroll-to-top'

export default function Pricing() {
  return (
    <>
        <NavBgWhite/>

        <section className="bg-cover bg-second" style={{backgroundImage:`url('/img/bg2.png')`, backgroundRepeat:'no-repeat'}}>
            <div className="container">
                <div className="row">
                    <div className="col-lg-12 col-md-12">
                        <h2 className="ipt-title text-light">Pricing Page</h2>
                        <span className="ipn-subtitle text-light opacity-75">Explore our Min Cost Packages</span>
                    </div>
                </div>
            </div>
        </section>

        <section>
            <div className="container">
                <PricingOne/>
            </div>
        </section>

        <FooterTopTwo/>

        <FooterLightTwo/>

        <ScrollToTop/>
    </>
  )
}
