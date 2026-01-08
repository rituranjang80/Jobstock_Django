
import Image from "next/image";
import HomeBannerCounter from "./components/counter/home-banner-counter";
import FormOne from "./components/form/form-one";
import Navlight from "./components/navbar/navlight";
import PartnerOne from "./components/partner/partner-one";
import FeatureJob from "./components/job/feature-job";
import CategoryOne from "./components/category/category-one";
import ProcessOne from "./components/process/process-one";
import CtaOne from "./components/cta/cta-one";
import ClientOne from "./components/client/client-one";
import SubscribeTwo from "./components/subscribe/subscribe-two";
import FooterOne from "./components/footer/footer-one";
import ScrollToTop from "./components/scroll-to-top";

export default function Home() {
  return (
      <>
        <Navlight/>

        <div className="image-cover hero-header position-relative py-5 p-150" style={{backgroundImage:`url('/img/4268.jpg')`, backgroundRepeat:'no-repeat'}} data-overlay="7">
            <div className="position-absolute bottom-0 start-0 end-0">
                <Image src='/img/banner-curve.svg' width={0} height={0} sizes="100vw" style={{width:'100%', height:'auto'}} className="img-fluid" alt="SVG"/>
            </div>
            <div className="container position-relative z-9">

                <div className="row justify-content-between align-items-center">
                    <div className="col-xl-6 col-lg-6 col-md-12 col-sm-12">
                        <h6 className="text-green fw-medium d-inline-flex align-items-center mb-3"><span className="bg-green w-10 h-05 me-2"></span>Get Hot & Trending Jobs</h6>
                        <h1 className="mb-4">Real Jobs, Real People, Real Success</h1>
                        <p className="fs-5">Getting a new job is never easy. Check what new jobs we have in store for you on JobStock.</p>
                        <div className="lios-vrst">
                            <HomeBannerCounter/>
                        </div>
                    </div>
                    
                    <div className="col-xl-5 col-lg-5 col-md-12 col-sm-12">
                        <div className="hero-search-wrap">
                            <div className="hero-search">
                                <h1>Grow Your Career with <span className="text-main">JobStock</span></h1>
                            </div>
                            <FormOne/>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <section className="min">
            <div className="container">
                <div className="row justify-content-center mb-2">
                    <div className="col-xl-4 col-lg-7 col-md-10 text-center">
                        <div className="center mb-4">
                            <h5 className="fw-medium lh-lg">Join over 2,000 companies around the world that trust the <span className="text-main">JobStock</span> platforms</h5>
                        </div>
                    </div>
                </div>
                <PartnerOne/>
            </div>
        </section>
        <div className="clearfix"></div>

        <section className="pt-2">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Featured Jobs</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <FeatureJob/>
            </div>
        </section>

        <section className="gray-simple">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Explore Top Categories</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <CategoryOne light={false}/>
            </div>
        </section>

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10">
                        <div className="sec-heading center">
                            <h2>Features & Process</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
               <ProcessOne/>
            </div>
        </section>

        <CtaOne/>

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Good Reviews By Customers</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
              <ClientOne/>
            </div>	
        </section>

        <SubscribeTwo/>

        <FooterOne/>

        <ScrollToTop/>
      </>
  );
}
